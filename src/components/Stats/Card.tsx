interface CardProps {
  title: string;
  value: string;
}

const Card = ({ title, value }: CardProps) => {
  return (
    <div>
      <div>
        <p className="text-xl tracking-wide font-bold text-oldLavender">
          {title}
        </p>
      </div>
      <div className="flex flex-row gap-4 items-end">
        <div>
          <p className="text-4xl tracking-wider ordinal">{value}</p>
        </div>
      </div>
    </div>
  );
};

export default Card;
